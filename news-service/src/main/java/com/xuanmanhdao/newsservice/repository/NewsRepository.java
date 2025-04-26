package com.xuanmanhdao.newsservice.repository;

import com.xuanmanhdao.newsservice.entity.NewsDocumentEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;

public interface NewsRepository extends ElasticsearchRepository<NewsDocumentEntity, String> {
    Page<NewsDocumentEntity> findByTitleContainingIgnoreCase(String title, Pageable pageable);
    Page<NewsDocumentEntity> findBySource(String source, Pageable pageable);
}
